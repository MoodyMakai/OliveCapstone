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

    var body: some Scene {
        WindowGroup {
            FoodshareListView()
                .environmentObject(store)
        }
    }
}

#Preview {
    FoodshareListView().environmentObject(FoodshareStore())
}
