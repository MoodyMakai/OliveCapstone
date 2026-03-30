//
//  SData.swift
//  BlackBearFoodShare
//

import Foundation
import Combine

var sampleFoodshareItems: [FoodshareItem] = [
    FoodshareItem(
        foodshare_id: 1,
        name: "Computer Science Club Pizza",
        location: "Neville Hall, Room 101",
        ends: ISO8601DateFormatter().string(from: Date().addingTimeInterval(3600)),
        active: true,
        creator: User(user_id: 1, email: "tester@maine.edu", is_admin: false),
        picture: PictureMetadata(filepath: "https://picsum.photos/200", mimetype: "image/jpeg"),
        restrictions: ["Vegan"]
    ),
    FoodshareItem(
        foodshare_id: 2,
        name: "Leftover Sandwiches",
        location: "DPC Hall, Room 107",
        ends: ISO8601DateFormatter().string(from: Date().addingTimeInterval(7200)),
        active: true,
        creator: User(user_id: 2, email: "tester2@maine.edu", is_admin: false),
        picture: PictureMetadata(filepath: "https://picsum.photos/200", mimetype: "image/jpeg"),
        restrictions: []
    )
]

class SData: ObservableObject {
    @Published var foodshareItems: [FoodshareItem] = sampleFoodshareItems
}
