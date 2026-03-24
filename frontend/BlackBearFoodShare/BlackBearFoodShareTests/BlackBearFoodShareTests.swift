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
        
        XCTAssertEqual(locator.address(for: "Neville Hall"), "98 Beddington Rd, Orono, ME 04473")
        
        XCTAssertNil(locator.address(for: "NonExistent"))
    }


    func testAliasesList() {
        let locator = BuildingLocator.shared

        let aliases = locator.allAliases()
        
        XCTAssertTrue(aliases.contains("Neville Hall"))
        XCTAssertTrue(aliases.contains("DPC Hall"))
        XCTAssertTrue(aliases.contains("Ferland Hall"))
    }
}
