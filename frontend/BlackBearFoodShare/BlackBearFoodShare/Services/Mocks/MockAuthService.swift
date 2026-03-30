//
//  MockAuthService.swift
//  BlackBearFoodShare
//

import Foundation

class MockAuthService: AuthServiceProtocol {
    var shouldError = false
    var lastRequestedEmail: String?
    var lastVerifiedOTP: String?
    var mockAuthResponse = AuthResponse(token: "mock-token", message: "Success")
    
    func requestOTP(email: String) async throws {
        if shouldError { throw BBFSError.serverError("Mock Error") }
        lastRequestedEmail = email
    }
    
    func verifyOTP(email: String, otp: String) async throws -> AuthResponse {
        if shouldError { throw BBFSError.unauthorized }
        lastVerifiedOTP = otp
        return mockAuthResponse
    }
    
    func logout() async throws {
        if shouldError { throw BBFSError.unknown }
    }
}
