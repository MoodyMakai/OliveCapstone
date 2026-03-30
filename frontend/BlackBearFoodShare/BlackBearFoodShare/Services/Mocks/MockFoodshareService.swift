//
//  MockFoodshareService.swift
//  BlackBearFoodShare
//

import Foundation

class MockFoodshareService: FoodshareServiceProtocol {
    var shouldError = false
    var mockItems: [FoodshareItem] = sampleFoodshareItems
    
    var lastCreatedItem: (name: String, location: String, ends: Date, restrictions: [String])?
    var lastDeletedID: Int?
    
    func fetchFoodshares() async throws -> [FoodshareItem] {
        if shouldError { throw BBFSError.serverError("Mock Fetch Error") }
        return mockItems
    }
    
    func createFoodshare(name: String, 
                         location: String, 
                         ends: Date, 
                         image: Data, 
                         restrictions: [String]) async throws -> FoodshareItem {
        if shouldError { throw BBFSError.serverError("Mock Create Error") }
        
        lastCreatedItem = (name, location, ends, restrictions)
        
        let newItem = FoodshareItem(
            foodshare_id: Int.random(in: 100...999),
            name: name,
            location: location,
            ends: ISO8601DateFormatter().string(from: ends),
            active: true,
            creator: User(user_id: 1, email: "preview@maine.edu", is_admin: false),
            picture: nil,
            restrictions: restrictions
        )
        return newItem
    }
    
    func closeFoodshare(id: Int) async throws {
        if shouldError { throw BBFSError.forbidden }
        lastDeletedID = id
    }
}
