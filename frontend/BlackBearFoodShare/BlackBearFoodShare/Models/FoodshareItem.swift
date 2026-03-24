//
//  FoodshareItem.swift
//  BlackBearFoodShare
//

import Foundation

enum DietaryRestriction: String, CaseIterable, Identifiable, Codable {
    case vegan = "Vegan"
    case vegetarian = "Vegetarian"
    case glutenFree = "Gluten-Free"
    case dairyFree = "Dairy-Free"
    case nutFree = "Nut-Free"
    case halal = "Halal"
    case kosher = "Kosher"

    var id: String { self.rawValue }
}

struct PictureMetadata: Codable {
    let filepath: String
    let mimetype: String
}

struct FoodshareItem: Codable, Identifiable {
    let foodshare_id: Int?
    let name: String
    let location: String
    let ends: String // ISO 8601 String from API
    let active: Bool?
    let creator: User?
    let picture: PictureMetadata?
    let restrictions: [String]
    
    var id: Int { foodshare_id ?? 0 }
    
    // UI Helpers
    var endTime: Date {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter.date(from: ends) ?? Date()
    }
}
