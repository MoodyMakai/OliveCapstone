//
//  MockAuthService.swift
//  BlackBearFoodShare
//

import Foundation

class MockAuthService: AuthServiceProtocol {
    var shouldError = false
    var lastRequestedEmail: String?
    var lastVerifiedOTP: String?
    var mockAuthResponse = AuthResponse(token: "mock-token", 
                                        message: "Success", 
                                        user: User(user_id: 1, email: "preview@maine.edu", is_admin: false))
    
    func requestOTP(email: String) async throws {
        if shouldError { throw BBFSError.serverError("Mock Error") }
        lastRequestedEmail = email
    }
    
    func verifyOTP(email: String, otp: String) async throws -> AuthResponse {
        if shouldError { throw BBFSError.unauthorized }
        lastVerifiedOTP = otp
        return mockAuthResponse
    }
    
    func fetchCurrentUser() async throws -> User {
        if shouldError { throw BBFSError.unauthorized }
        return User(user_id: 1, email: "preview@maine.edu", is_admin: false)
    }
    
    func logout() async throws {
        if shouldError { throw BBFSError.unknown }
    }
}
