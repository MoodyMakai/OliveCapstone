//
//  OTPVerifyView.swift
//  BlackBearFoodShare
//

import SwiftUI

@MainActor
struct OTPVerifyView: View {
    @StateObject private var viewModel: OTPVerifyViewModel
    
    init(email: String, viewModel: @autoclosure @escaping () -> OTPVerifyViewModel? = nil) {
        if let providedVM = viewModel() {
            _viewModel = StateObject(wrappedValue: providedVM)
        } else {
            _viewModel = StateObject(wrappedValue: OTPVerifyViewModel(email: email))
        }
    }
    
    var body: some View {
        VStack(spacing: 30) {
            VStack(spacing: 12) {
                Text("Verify Email")
                    .font(.title)
                    .bold()
                
                Text("We've sent a code to \(viewModel.email)")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            .padding(.top, 50)
            
            TextField("6-digit code", text: $viewModel.otp)
                .font(.largeTitle)
                .multilineTextAlignment(.center)
                .keyboardType(.numberPad)
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)
            
            if let error = viewModel.errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .font(.caption)
            }
            
            PrimaryButton("Verify", isLoading: viewModel.isLoading) {
                viewModel.verifyOTP()
            }
            .padding(.horizontal)
            .disabled(viewModel.isLoading || viewModel.otp.count != 6)
            
            Spacer()
        }
        .navigationTitle("OTP Verification")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    let mockService = MockAuthService()
    let viewModel = OTPVerifyViewModel(email: "test@maine.edu", authService: mockService)
    
    OTPVerifyView(email: "test@maine.edu", viewModel: viewModel)
        .environmentObject(SessionManager.shared)
}
