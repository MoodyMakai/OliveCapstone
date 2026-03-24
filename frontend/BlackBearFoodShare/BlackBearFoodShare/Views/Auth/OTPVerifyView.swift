//
//  OTPVerifyView.swift
//  BlackBearFoodShare
//

import SwiftUI

struct OTPVerifyView: View {
    @StateObject private var viewModel: OTPVerifyViewModel
    
    init(email: String) {
        _viewModel = StateObject(wrappedValue: OTPVerifyViewModel(email: email))
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
