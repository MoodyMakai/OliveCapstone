//
//  SessionManager.swift
//  BlackBearFoodShare
//

import Foundation
import SwiftUI
import Combine

@MainActor
class SessionManager: ObservableObject {
    static var shared = SessionManager()
    
    // For UI Testing and Previews
    static var preview: SessionManager {
        let manager = SessionManager(isAuthenticated: true, authService: MockAuthService())
        manager.currentUser = User(user_id: 1, email: "preview@maine.edu", is_admin: false)
        return manager
    }
    
    private let service = "ofs.BlackBearFoodShare"
    private let account = "authToken"
    
    @Published var isAuthenticated: Bool = false
    @Published var currentUser: User?
    
    private let authService: AuthServiceProtocol
    
    internal init(isAuthenticated: Bool? = nil, authService: AuthServiceProtocol = AuthService()) {
        self.authService = authService
        if let isAuthenticated = isAuthenticated {
            self.isAuthenticated = isAuthenticated
        } else {
            checkSession()
        }
    }
    
    func checkSession() {
        if let _ = KeychainHelper.shared.read(service: service, account: account) {
            isAuthenticated = true
            
            // Fetch current user profile to ensure isOwner checks work
            Task {
                do {
                    self.currentUser = try await authService.fetchCurrentUser()
                } catch {
                    print("Failed to fetch current user: \(error)")
                    // If fetching profile fails (e.g., token expired), we should probably logout
                    if let bbfsError = error as? BBFSError, case .unauthorized = bbfsError {
                        logout()
                    }
                }
            }
        } else {
            isAuthenticated = false
        }
    }
    
    func saveToken(_ token: String) {
        if let data = token.data(using: .utf8) {
            KeychainHelper.shared.save(data, service: service, account: account)
            isAuthenticated = true
        }
    }
    
    func getToken() -> String? {
        guard let data = KeychainHelper.shared.read(service: service, account: account) else { return nil }
        return String(data: data, encoding: .utf8)
    }
    
    func logout() {
        KeychainHelper.shared.delete(service: service, account: account)
        isAuthenticated = false
        currentUser = nil
    }
}
