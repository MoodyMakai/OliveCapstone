//
//  BBFSError.swift
//  BlackBearFoodShare
//

import Foundation

enum BBFSError: LocalizedError {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
    case unauthorized
    case forbidden
    case rateLimited
    case serverError(String)
    case validationError(String)
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Something went wrong with the application's connection settings."
        case .networkError: return "No internet connection. Please check your network and try again."
        case .invalidResponse: return "The server is temporarily unavailable. Please try again later."
        case .decodingError: return "We encountered an issue processing the server's response."
        case .unauthorized: return "Your session has expired. Please log in again."
        case .forbidden: return "You don't have permission to perform this action."
        case .rateLimited: return "Too many requests. Please wait a moment and try again."
        case .serverError: return "A server error occurred. Our team has been notified."
        case .validationError(let msg):
            if msg.contains("email") || msg.contains("@maine.edu") {
                return "Please enter a valid @maine.edu email address."
            } else if msg.contains("OTP") || msg.contains("expired") {
                return "The verification code is invalid or has expired. Please try again."
            } else if msg.contains("banned") {
                return "Your account has been suspended. Contact support for more info."
            }
            return msg
        case .unknown: return "An unexpected error occurred. Please try again."
        }
    }
}
