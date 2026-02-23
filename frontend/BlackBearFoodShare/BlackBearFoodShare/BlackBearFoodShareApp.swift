//
//  BlackBearFoodShareApp.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 11/24/25.
//

import SwiftUI

@main
struct MyApp: App {
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
