//
//  SData.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 12/1/25.
//

import Foundation
import SwiftUI
internal import Combine

var sampleFoodshareItems = [
    FoodshareItem(
        name: "Computer Science Club Pizza",
        endTime: Date().addingTimeInterval(3600),
        description: "Pizza and breadsticks",
        foodRestrictions: ["Vegan"],
        imageURL: "https://picsum.photos/200",
        building: "Neville Hall",
        classRoomNumber: "101"
    ),
    FoodshareItem(
        name: "Leftover Sandwiches",
        endTime: Date().addingTimeInterval(7200),
        description: "Ham and cheese sandwiches",
        foodRestrictions: [],
        imageURL: "https://picsum.photos/200",
        building: "DPC Hall",
        classRoomNumber: "107"
    ),
    FoodshareItem(
        name: "Extra Popcorn",
        endTime: Date().addingTimeInterval(5400),
        description: "Buttered and kettle corn",
        foodRestrictions: [],
        imageURL: "https://picsum.photos/200",
        building: "Ferland Hall",
        classRoomNumber: "114"
    )
]
class SData: ObservableObject {
    @Published var foodshareItems: [FoodshareItem] = sampleFoodshareItems
}
