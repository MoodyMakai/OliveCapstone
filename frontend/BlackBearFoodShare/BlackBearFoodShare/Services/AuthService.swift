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
        
        try await NetworkManager.shared.request("/auth/request-otp", method: "POST", body: data, requiresAuth: false)
    }
    
    func verifyOTP(email: String, otp: String) async throws -> AuthResponse {
        let body: [String: String] = ["email": email, "otp": otp]
        let data = try JSONEncoder().encode(body)
        
        return try await NetworkManager.shared.request("/auth/verify-otp", method: "POST", body: data, requiresAuth: false)
    }
    
    func logout() async throws {
        try await NetworkManager.shared.request("/auth/logout", method: "POST", requiresAuth: true)
    }
}
