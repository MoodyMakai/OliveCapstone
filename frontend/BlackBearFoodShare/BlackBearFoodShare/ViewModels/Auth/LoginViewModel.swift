//
//  LoginViewModel.swift
//  BlackBearFoodShare
//

import Foundation
import SwiftUI
import Combine

@MainActor
class LoginViewModel: ObservableObject {
    @Published var email: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var navigateToOTP: Bool = false
    
    private let authService: AuthServiceProtocol
    
    init(authService: AuthServiceProtocol) {
        self.authService = authService
    }
    
    convenience init() {
        self.init(authService: AuthService())
    }
    
    func requestOTP() {
        guard email.lowercased().hasSuffix("@maine.edu") else {
            errorMessage = "Please use a @maine.edu email address."
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                try await authService.requestOTP(email: email)
                navigateToOTP = true
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}
