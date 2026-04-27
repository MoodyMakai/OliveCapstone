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
    
    func testOTPVerifyViewModel_Success() async {
        let mockService = MockAuthService()
        let viewModel = OTPVerifyViewModel(email: "test@maine.edu", authService: mockService)
        viewModel.otp = "123456"
        
        viewModel.verifyOTP()
        
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        XCTAssertEqual(mockService.lastVerifiedOTP, "123456")
        XCTAssertNil(viewModel.errorMessage)
    }
    
    func testOTPVerifyViewModel_InvalidFormat() {
        let viewModel = OTPVerifyViewModel(email: "test@maine.edu", authService: MockAuthService())
        viewModel.otp = "123"
        
        viewModel.verifyOTP()
        
        XCTAssertNotNil(viewModel.errorMessage)
        XCTAssertEqual(viewModel.errorMessage, "OTP must be 6 digits.")
    }
}
