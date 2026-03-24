//
//  AuthService.swift
//  BlackBearFoodShare
//

import Foundation
import Combine

class AuthService: AuthServiceProtocol {
    func requestOTP(email: String) async throws {
        let body: [String: String] = ["email": email]
        let data = try JSONEncoder().encode(body)
        
        // request expects no return body on success usually, 
        // but our NetworkManager expects a Decodable.
        // We can use a Dummy Decodable or update NetworkManager.
        struct Dummy: Decodable {}
        let _: Dummy = try await NetworkManager.shared.request("/auth/request-otp", method: "POST", body: data, requiresAuth: false)
    }
    
    func verifyOTP(email: String, otp: String) async throws -> AuthResponse {
        let body: [String: String] = ["email": email, "otp": otp]
        let data = try JSONEncoder().encode(body)
        
        let response: AuthResponse = try await NetworkManager.shared.request("/auth/verify-otp", method: "POST", body: data, requiresAuth: false)
        return response
    }
    
    func logout() async throws {
        struct Dummy: Decodable {}
        let _: Dummy = try await NetworkManager.shared.request("/auth/logout", method: "POST", requiresAuth: true)
    }
}
