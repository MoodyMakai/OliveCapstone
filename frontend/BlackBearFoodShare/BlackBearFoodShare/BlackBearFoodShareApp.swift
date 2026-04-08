//
//  BlackBearFoodShareApp.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 11/24/25.
//

import SwiftUI
import UIKit

@main
struct MyApp: App {

    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    @StateObject var store: FoodshareStore
    @StateObject var session: SessionManager

    init() {
        if ProcessInfo.processInfo.arguments.contains("-UITest") {
            let mockAuth = MockAuthService()
            
            let sessionManager = SessionManager(isAuthenticated: false, authService: mockAuth)
            _session = StateObject(wrappedValue: sessionManager)
            
            // For convenience elsewhere if needed
            SessionManager.shared = sessionManager
            
            _store = StateObject(wrappedValue: FoodshareStore())
            
            // Clear any existing session for a clean test state
            sessionManager.logout()
        } else {
            _session = StateObject(wrappedValue: SessionManager.shared)
            _store = StateObject(wrappedValue: FoodshareStore())
        }
    }

    var body: some Scene {
        WindowGroup {
            if session.isAuthenticated {
                FoodshareListView()
                    .environmentObject(store)
                    .environmentObject(session)
            } else {
                LoginView()
                    .environmentObject(session)
            }
        }
    }
}

#Preview {
    FoodshareListView()
        .environmentObject(FoodshareStore())
        .environmentObject(SessionManager.preview)
}
