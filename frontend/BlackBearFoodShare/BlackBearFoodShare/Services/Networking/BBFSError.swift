//
//  BBFSError.swift
//  BlackBearFoodShare
//

import Foundation

enum BBFSError: LocalizedError {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
    case unauthorized
    case forbidden
    case rateLimited
    case serverError(String)
    case validationError(String)
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "The URL provided was invalid."
        case .networkError(let error): return "Network error: \(error.localizedDescription)"
        case .invalidResponse: return "Received an invalid response from the server."
        case .decodingError: return "Failed to decode the data from the server."
        case .unauthorized: return "You are not authorized. Please log in again."
        case .forbidden: return "You do not have permission to perform this action."
        case .rateLimited: return "Too many requests. Please wait and try again later."
        case .serverError(let msg): return "Server error: \(msg)"
        case .validationError(let msg): return "Validation error: \(msg)"
        case .unknown: return "An unknown error occurred."
        }
    }
}
