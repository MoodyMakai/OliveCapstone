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

    @StateObject var store = FoodshareStore()

    @StateObject var session = SessionManager.shared

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
    FoodshareListView().environmentObject(FoodshareStore())
}
