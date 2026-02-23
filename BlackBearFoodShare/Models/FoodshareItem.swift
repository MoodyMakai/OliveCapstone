//
//  FoodshareItem.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 12/1/25.
//


import Foundation

enum DietaryRestriction: String, CaseIterable, Identifiable {
    case vegan = "Vegan"
    case vegetarian = "Vegetarian"
    case glutenFree = "Gluten-Free"
    case dairyFree = "Dairy-Free"
    case nutFree = "Nut-Free"
    case halal = "Halal"
    case kosher = "Kosher"

    var id: String { self.rawValue }
}

struct FoodshareItem: Identifiable {
    let id = UUID()
    let name: String
    let endTime: Date
    let description: String
    let foodRestrictions: Array<String>
    let imageURL: String
    let building: String
    let classRoomNumber: String
}
