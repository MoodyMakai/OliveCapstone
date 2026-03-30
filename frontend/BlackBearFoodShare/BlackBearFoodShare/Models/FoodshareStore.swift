//
//  FoodshareStore.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 12/7/25.
//

import SwiftUI
import Combine

@MainActor
class FoodshareStore: ObservableObject {
    @Published var items: [FoodshareItem] = []

    func add(_ item: FoodshareItem) {
        items.append(item)
    }
    
    func delete(_ item: FoodshareItem) {
        items.removeAll { $0.id == item.id }
    }
}
