//
//  AuthViewModelTests.swift
//  BlackBearFoodShareTests
//

import XCTest
@testable import BlackBearFoodShare

@MainActor
class AuthViewModelTests: XCTestCase {
    
    func testLoginViewModel_RequestOTP_Success() async {
        let mockService = MockAuthService()
        let viewModel = LoginViewModel(authService: mockService)
        viewModel.email = "test@maine.edu"
        
        viewModel.requestOTP()
        
        // Give the task a moment to execute or use a proper expectation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        XCTAssertTrue(viewModel.navigateToOTP)
        XCTAssertEqual(mockService.lastRequestedEmail, "test@maine.edu")
        XCTAssertNil(viewModel.errorMessage)
    }
    
    func testLoginViewModel_InvalidEmail() {
        let viewModel = LoginViewModel(authService: MockAuthService())
        viewModel.email = "hacker@gmail.com"
        
        viewModel.requestOTP()
        
        XCTAssertFalse(viewModel.navigateToOTP)
        XCTAssertNotNil(viewModel.errorMessage)
    }
}
