//
//  FoodshareFeedViewModelTests.swift
//  BlackBearFoodShareTests
//

import XCTest
@testable import BlackBearFoodShare

@MainActor
class FoodshareFeedViewModelTests: XCTestCase {
    
    class MockFoodshareService: FoodshareServiceProtocol {
        var itemsToReturn: [FoodshareItem] = []
        var shouldError = false
        
        func fetchFoodshares() async throws -> [FoodshareItem] {
            if shouldError { throw BBFSError.serverError("Fetch Error") }
            return itemsToReturn
        }
        
        func createFoodshare(name: String, location: String, ends: Date, image: Data, restrictions: [String]) async throws -> FoodshareItem {
            return itemsToReturn[0]
        }
        
        func closeFoodshare(id: Int) async throws {}
        
        func submitSurvey(_ survey: Survey) async throws {}
    }
    
    func testLoadItems_Success() async {
        let mockService = MockFoodshareService()
        mockService.itemsToReturn = [
            FoodshareItem(foodshare_id: 1, name: "Test", location: "Loc", ends: "2024-01-01T00:00:00Z", active: true, creator: nil, picture: nil, restrictions: [])
        ]
        
        let viewModel = FoodshareFeedViewModel(service: mockService)
        viewModel.loadItems()
        
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        XCTAssertEqual(viewModel.items.count, 1)
        XCTAssertEqual(viewModel.items.first?.name, "Test")
        XCTAssertNil(viewModel.errorMessage)
    }
    
    func testLoadItems_Failure() async {
        let mockService = MockFoodshareService()
        mockService.shouldError = true
        
        let viewModel = FoodshareFeedViewModel(service: mockService)
        viewModel.loadItems()
        
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        XCTAssertEqual(viewModel.items.count, 0)
        XCTAssertNotNil(viewModel.errorMessage)
    }
}
