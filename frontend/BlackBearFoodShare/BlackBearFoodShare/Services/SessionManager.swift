//
//  SessionManager.swift
//  BlackBearFoodShare
//

import Foundation
import SwiftUI
import Combine

@MainActor
class SessionManager: ObservableObject {
    static let shared = SessionManager()
    
    private let service = "ofs.BlackBearFoodShare"
    private let account = "authToken"
    
    @Published var isAuthenticated: Bool = false
    @Published var currentUser: User?
    
    private init() {
        checkSession()
    }
    
    func checkSession() {
        if let _ = KeychainHelper.shared.read(service: service, account: account) {
            isAuthenticated = true
            // In a real app, we might also store/read the User object or fetch it from the API
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
