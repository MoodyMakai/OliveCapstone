//
//  NetworkManager.swift
//  BlackBearFoodShare
//

import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    
    private let baseURL: String
    private let session = URLSession.shared
    
    private init() {
        // Load API_BASE_URL from Info.plist
        guard let urlString = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String else {
            fatalError("API_BASE_URL not found in Info.plist")
        }
        self.baseURL = urlString.replacingOccurrences(of: "\\", with: "")
    }
    
    /// Request returning a Decodable object
    func request<T: Decodable>(_ endpoint: String, 
                               method: String = "GET", 
                               body: Data? = nil, 
                               requiresAuth: Bool = true) async throws -> T {
        
        let (data, _) = try await performRequest(endpoint, method: method, body: body, requiresAuth: requiresAuth)
        
        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .custom { decoder in
                let container = try decoder.singleValueContainer()
                let dateStr = try container.decode(String.self)
                let formatter = ISO8601DateFormatter()
                formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
                if let date = formatter.date(from: dateStr) {
                    return date
                }
                // Try without fractional seconds if first attempt fails
                formatter.formatOptions = [.withInternetDateTime]
                if let date = formatter.date(from: dateStr) {
                    return date
                }
                throw DecodingError.dataCorruptedError(in: container, debugDescription: "Invalid date format: \(dateStr)")
            }
            return try decoder.decode(T.self, from: data)
        } catch {
            throw BBFSError.decodingError(error)
        }
    }

    /// Request returning no body (Void)
    func request(_ endpoint: String, 
                  method: String = "GET", 
                  body: Data? = nil, 
                  requiresAuth: Bool = true) async throws {
        _ = try await performRequest(endpoint, method: method, body: body, requiresAuth: requiresAuth)
    }

    private func performRequest(_ endpoint: String, 
                                method: String, 
                                body: Data?, 
                                requiresAuth: Bool) async throws -> (Data, HTTPURLResponse) {
        
        guard let url = URL(string: baseURL + endpoint) else {
            throw BBFSError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if requiresAuth {
            if let token = SessionManager.shared.getToken() {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
        }
        
        if let body = body {
            request.httpBody = body
        }
        
        let data: Data
        let response: URLResponse
        
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw BBFSError.networkError(error)
        }
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw BBFSError.invalidResponse
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            return (data, httpResponse)
        case 401: throw BBFSError.unauthorized
        case 403: throw BBFSError.forbidden
        case 429: throw BBFSError.rateLimited
        case 400, 404, 422:
            // Extract backend error message if available
            let errorMsg: String
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let message = json["error"] as? String {
                errorMsg = message
            } else {
                errorMsg = String(data: data, encoding: .utf8) ?? "Validation failed"
            }
            throw BBFSError.validationError(errorMsg)
        case 500:
            throw BBFSError.serverError("Internal Server Error")
        default:
            throw BBFSError.unknown
        }
    }
    
    // Support for multipart/form-data for image uploads
    func upload<T: Decodable>(_ endpoint: String, 
                                parameters: [String: String], 
                                image: Data, 
                                fileName: String) async throws -> T {
        
        guard let url = URL(string: baseURL + endpoint) else {
            throw BBFSError.invalidURL
        }
        
        let boundary = "Boundary-\(UUID().uuidString)"
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        if let token = SessionManager.shared.getToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        var body = Data()
        
        for (key, value) in parameters {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(value)\r\n".data(using: .utf8)!)
        }
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"picture\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/webp\r\n\r\n".data(using: .utf8)!)
        body.append(image)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        let data: Data
        let response: URLResponse
        
        do {
            (data, response) = try await session.upload(for: request, from: body)
        } catch {
            throw BBFSError.networkError(error)
        }
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw BBFSError.invalidResponse
        }
        
        if httpResponse.statusCode == 200 || httpResponse.statusCode == 201 {
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .custom { decoder in
                    let container = try decoder.singleValueContainer()
                    let dateStr = try container.decode(String.self)
                    let formatter = ISO8601DateFormatter()
                    formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
                    if let date = formatter.date(from: dateStr) {
                        return date
                    }
                    formatter.formatOptions = [.withInternetDateTime]
                    if let date = formatter.date(from: dateStr) {
                        return date
                    }
                    throw DecodingError.dataCorruptedError(in: container, debugDescription: "Invalid date format: \(dateStr)")
                }
                return try decoder.decode(T.self, from: data)
            } catch {
                throw BBFSError.decodingError(error)
            }
        } else {
            let errorMsg: String
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let message = json["error"] as? String {
                errorMsg = message
            } else {
                errorMsg = "Upload failed with status \(httpResponse.statusCode)"
            }
            throw BBFSError.validationError(errorMsg)
        }
    }
}
