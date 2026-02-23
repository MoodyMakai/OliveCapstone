//
//  BlackBearFoodShareTests.swift
//  BlackBearFoodShareTests
//
//  Created by Corey Kaulenas on 11/24/25.
//

import XCTest
import Testing
@testable import BlackBearFoodShare

struct BlackBearFoodShareTests {

    @Test func example() async throws {
        // Write your test here and use APIs like `#expect(...)` to check expected conditions.
    }

}

final class BuildingLocatorTests: XCTestCase {

    func testAddressLookup() {
        let locator = BuildingLocator.shared
        
        XCTAssertEqual(locator.address(for: "Neville Hall"), "98 Beddington Rd, Orono, ME 04473 United States")
        
        XCTAssertNil(locator.address(for: "NonExistent"))
    }

    func testMapsURL() {
        let locator = BuildingLocator.shared

        let url = locator.mapsURL(for: "DPC Hall")
        XCTAssertNotNil(url)
        XCTAssert(url!.absoluteString.contains("29%20Beddington%20Rd,%20Orono,%20ME%2004469"))
    }

    func testAliasesList() {
        let locator = BuildingLocator.shared

        let aliases = locator.allAliases()
        
        XCTAssertTrue(aliases.contains("Neville Hall"))
        XCTAssertTrue(aliases.contains("DPC Hall"))
        XCTAssertTrue(aliases.contains("Ferland Hall"))
    }
}
