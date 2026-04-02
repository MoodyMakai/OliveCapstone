//
//  FoodshareServiceProtocol.swift
//  BlackBearFoodShare
//

import Foundation
import Combine

protocol FoodshareServiceProtocol {
    func fetchFoodshares() async throws -> [FoodshareItem]
    func createFoodshare(name: String, 
                         location: String, 
                         ends: Date, 
                         image: Data, 
                         restrictions: [String]) async throws -> FoodshareItem
    func closeFoodshare(id: Int) async throws
    func submitSurvey(_ survey: Survey) async throws
}
