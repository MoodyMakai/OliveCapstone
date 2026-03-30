//
//  LoginView.swift
//  BlackBearFoodShare
//

import SwiftUI

@MainActor
struct LoginView: View {
    @StateObject private var viewModel: LoginViewModel
    
    init(viewModel: @autoclosure @escaping () -> LoginViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel())
    }
    
    init() {
        self.init(viewModel: LoginViewModel())
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                VStack(spacing: 12) {
                    Image(systemName: "hand.raised.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.blue)
                    
                    Text("Black Bear Foodshare")
                        .font(.title)
                        .bold()
                }
                .padding(.top, 50)
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("Email Address")
                        .font(.headline)
                    
                    TextField("Enter your @maine.edu email", text: $viewModel.email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                }
                .padding(.horizontal)
                
                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }
                
                PrimaryButton("Send OTP", isLoading: viewModel.isLoading) {
                    viewModel.requestOTP()
                }
                .padding(.horizontal)
                .disabled(viewModel.isLoading)
                
                NavigationLink(
                    destination: OTPVerifyView(email: viewModel.email),
                    isActive: $viewModel.navigateToOTP,
                    label: { EmptyView() }
                )
                
                Spacer()
            }
            .navigationBarHidden(true)
        }
    }
}

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        let mockService = MockAuthService()
        let viewModel = LoginViewModel(authService: mockService)
        
        LoginView(viewModel: viewModel)
            .environmentObject(SessionManager.shared)
    }
}
