//
//  BuildingAddressItem.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 12/7/25.
//

import Foundation
import MapKit
import CoreLocation

struct BuildingInfo {
    let address: String
    let coordinate: CLLocationCoordinate2D
}

class BuildingLocator {
    static let shared = BuildingLocator()
    
    private init() {}
    
    // Dictionary mapping names to Data
    // NOTE: Coordinate Format is (Latitude, Longitude)
    private let buildings: [String: BuildingInfo] = [
        "Ferland Hall": BuildingInfo(
            address: "75 Long Rd, Orono, ME 04469",
            coordinate: CLLocationCoordinate2D(latitude: 44.90245165547136, longitude: -68.66826684585462)
        ),
        "Neville Hall": BuildingInfo(
            address: "98 Beddington Rd, Orono, ME 04473",
            coordinate: CLLocationCoordinate2D(latitude: 44.9021069559729, longitude: -68.66769620352535)
        ),
        "DPC Hall": BuildingInfo(
            address: "29 Beddington Rd, Orono, ME 04469",
            coordinate: CLLocationCoordinate2D(latitude: 44.90015986140914, longitude: -68.66660549003154)
        )
    ]
    
    
    // Returns a sorted list of all building names
    public func allAliases() -> [String] {
        buildings.keys.sorted()
    }
    
    // Returns the display address string
    public func address(for alias: String) -> String? {
        findBuilding(alias)?.address
    }
    
    // Returns the exact coordinate
    public func coordinate(for alias: String) -> CLLocationCoordinate2D? {
        findBuilding(alias)?.coordinate
    }
    
    // Returns a URL that opens Apple Maps using EXACT coordinates
    func mapsURL(for alias: String) -> URL? {
        guard let info = findBuilding(alias) else { return nil }
        
        // We use 'daddr' with Lat,Long to ensure exact navigation
        let lat = info.coordinate.latitude
        let long = info.coordinate.longitude
        
        // "daddr" = Destination Address.
        // "q" = Label for the pin (so it says "Ferland Hall" instead of "Dropped Pin")
        let label = alias.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let urlString = "https://maps.apple.com/?daddr=\(lat),\(long)&q=\(label)"
        
        return URL(string: urlString)
    }
    
    // Helper to handle case-insensitive lookup
    private func findBuilding(_ alias: String) -> BuildingInfo? {
        let searchKey = alias.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        
        for (key, info) in buildings {
            if key.lowercased() == searchKey {
                return info
            }
        }
        return nil
    }
}
