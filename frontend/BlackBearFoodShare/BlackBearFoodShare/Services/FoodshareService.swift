//
//  FoodshareService.swift
//  BlackBearFoodShare
//

import Foundation
import Combine

class FoodshareService: FoodshareServiceProtocol {
    func fetchFoodshares() async throws -> [FoodshareItem] {
        return try await NetworkManager.shared.request("/foodshares", method: "GET")
    }
    
    func createFoodshare(name: String, 
                         location: String, 
                         ends: Date, 
                         image: Data, 
                         restrictions: [String]) async throws -> FoodshareItem {
        
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        
        let parameters: [String: String] = [
            "name": name,
            "location": location,
            "ends": formatter.string(from: ends),
            "picture_expires": formatter.string(from: ends), // Sync image expiry with food expiry
            "active": "true",
            "restrictions": restrictions.joined(separator: ",")
        ]
        
        return try await NetworkManager.shared.upload("/foodshares", 
                                                    parameters: parameters, 
                                                    image: image, 
                                                    fileName: "upload.webp")
    }
    
    func closeFoodshare(id: Int) async throws {
        let body: [String: Int] = ["foodshare_id": id]
        let data = try JSONEncoder().encode(body)
        
        try await NetworkManager.shared.request("/foodshares/close", method: "POST", body: data)
    }
    
    func submitSurvey(_ survey: Survey) async throws {
        let data = try JSONEncoder().encode(survey)
        try await NetworkManager.shared.request("/surveys", method: "POST", body: data)
    }
}
