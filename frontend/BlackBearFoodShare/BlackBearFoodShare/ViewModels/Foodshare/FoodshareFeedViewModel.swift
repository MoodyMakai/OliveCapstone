//
//  FoodshareFeedViewModel.swift
//  BlackBearFoodShare
//

import Foundation
import SwiftUI
import Combine

@MainActor
class FoodshareFeedViewModel: ObservableObject {
    @Published var items: [FoodshareItem] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    private let service: FoodshareServiceProtocol
    
    init(service: FoodshareServiceProtocol) {
        self.service = service
    }
    
    convenience init() {
        if ProcessInfo.processInfo.arguments.contains("-UITest") {
            self.init(service: MockFoodshareService())
        } else {
            self.init(service: FoodshareService())
        }
    }
    
    func loadItems() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                items = try await service.fetchFoodshares()
            } catch {
                errorMessage = error.localizedDescription
                // For now, if API fails (e.g. localhost not running), we could keep items as empty
            }
            isLoading = false
        }
    }
    
    func deleteItem(_ item: FoodshareItem) {
        guard let id = item.foodshare_id else { return }
        
        Task {
            do {
                try await service.closeFoodshare(id: id)
                items.removeAll { $0.id == item.id }
            } catch {
                errorMessage = "Could not close foodshare: \(error.localizedDescription)"
            }
        }
    }
}
