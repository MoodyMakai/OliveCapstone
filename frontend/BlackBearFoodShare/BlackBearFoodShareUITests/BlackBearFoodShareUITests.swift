//
//  BlackBearFoodShareUITests.swift
//  BlackBearFoodShareUITests
//
//  Created by Corey Kaulenas on 11/24/25.
//

import XCTest

final class BlackBearFoodShareUITests: XCTestCase {

    override func setUpWithError() throws {
        // Put setup code here. This method is called before the invocation of each test method in the class.

        // In UI tests it is usually best to stop immediately when a failure occurs.
        continueAfterFailure = false

        // In UI tests it’s important to set the initial state - such as interface orientation - required for your tests before they run. The setUp method is a good place to do this.
    }

    override func tearDownWithError() throws {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
    }

    @MainActor
    func testPostFoodshareJourney() throws {
        let app = XCUIApplication()
        app.launchArguments.append("-UITest")
        app.launch()

        // 1. Login
        let emailField = app.textFields["Enter your @maine.edu email"]
        XCTAssertTrue(emailField.waitForExistence(timeout: 5))
        emailField.tap()
        emailField.typeText("test@maine.edu")
        
        app.buttons["Send OTP"].tap()
        
        // 2. Verify OTP
        let otpField = app.textFields["6-digit code"]
        XCTAssertTrue(otpField.waitForExistence(timeout: 5))
        otpField.tap()
        otpField.typeText("123456")
        
        app.buttons["Verify"].tap()
        
        // 3. Create Foodshare
        let plusButton = app.buttons["plus"]
        XCTAssertTrue(plusButton.waitForExistence(timeout: 5))
        plusButton.tap()
        
        let nameField = app.textFields["Name (e.g. Free Pizza)"]
        XCTAssertTrue(nameField.waitForExistence(timeout: 5))
        nameField.tap()
        nameField.typeText("CI Test Pizza")
        
        // Select building
        app.staticTexts["Select a building"].tap()
        app.buttons["Neville Hall"].tap()
        
        app.buttons["Create Foodshare"].tap()
        
        // 4. Verify it appears in the list (MockService adds it to sample data)
        XCTAssertTrue(app.staticTexts["CI Test Pizza"].waitForExistence(timeout: 5))
    }

    @MainActor
    func testLaunchPerformance() throws {
        // This measures how long it takes to launch your application.
        measure(metrics: [XCTApplicationLaunchMetric()]) {
            XCUIApplication().launch()
        }
    }
}
