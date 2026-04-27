//
//  Survey.swift
//  BlackBearFoodShare
//

import Foundation

struct Survey: Codable {
    let num_participants: Int
    let experience: Int
    let other_thoughts: String
    let foodshare_fk_id: Int
}
