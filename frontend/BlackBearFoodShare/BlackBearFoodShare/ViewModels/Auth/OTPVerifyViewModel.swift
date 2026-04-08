//
//  OTPVerifyViewModel.swift
//  BlackBearFoodShare
//

import Foundation
import SwiftUI
import Combine

@MainActor
class OTPVerifyViewModel: ObservableObject {
    
    let email: String
    @Published var otp: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    private let authService: AuthServiceProtocol
    
    init(email: String, authService: AuthServiceProtocol) {
        self.email = email
        self.authService = authService
        self.isLoading = false
    }
    
    convenience init(email: String) {
        if ProcessInfo.processInfo.arguments.contains("-UITest") {
            self.init(email: email, authService: MockAuthService())
        } else {
            self.init(email: email, authService: AuthService())
        }
    }
    
    func verifyOTP() {
        guard otp.count == 6 else {
            errorMessage = "OTP must be 6 digits."
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let response = try await authService.verifyOTP(email: email, otp: otp)
                SessionManager.shared.saveToken(response.token)
                SessionManager.shared.currentUser = response.user
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}
