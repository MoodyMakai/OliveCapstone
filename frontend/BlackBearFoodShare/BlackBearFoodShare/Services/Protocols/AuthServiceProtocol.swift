//
//  AuthServiceProtocol.swift
//  BlackBearFoodShare
//

import Foundation
import Combine

protocol AuthServiceProtocol {
    func requestOTP(email: String) async throws
    func verifyOTP(email: String, otp: String) async throws -> AuthResponse
    func fetchCurrentUser() async throws -> User
    func logout() async throws
}
