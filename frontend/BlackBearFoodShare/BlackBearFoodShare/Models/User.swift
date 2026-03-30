//
//  User.swift
//  BlackBearFoodShare
//

import Foundation

struct User: Codable, Identifiable {
    let user_id: Int
    let email: String
    let is_admin: Bool?
    
    var id: Int { user_id }
}
