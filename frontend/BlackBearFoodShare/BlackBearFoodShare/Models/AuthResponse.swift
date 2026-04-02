//
//  AuthResponse.swift
//  BlackBearFoodShare
//

import Foundation

struct AuthResponse: Codable {
    let token: String
    let message: String
    let user: User?
}
