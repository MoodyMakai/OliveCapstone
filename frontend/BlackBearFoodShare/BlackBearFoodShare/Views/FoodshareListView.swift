//
//  FoodshareListView.swift
//  BlackBearFoodShare
//

import SwiftUI

struct FoodshareListView: View {
    @StateObject private var viewModel = FoodshareFeedViewModel()
    @EnvironmentObject var session: SessionManager
    
    @State private var showingCreate = false
    @State private var activeFilter: DietaryRestriction? = nil
    
    // Computed property to filter the list dynamically
    var filteredItems: [FoodshareItem] {
        if let filter = activeFilter {
            return viewModel.items.filter { $0.restrictions.contains(filter.rawValue) }
        }
        return viewModel.items
    }

    var body: some View {
        NavigationView {
            ZStack {
                if viewModel.isLoading && viewModel.items.isEmpty {
                    ProgressView("Loading Foodshares...")
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error, retryAction: viewModel.loadItems)
                } else if viewModel.items.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "takeoutbag.and.cup.and.straw")
                            .font(.system(size: 60))
                            .foregroundColor(.secondary)
                        Text("No active foodshares at the moment.")
                            .font(.headline)
                            .foregroundColor(.secondary)
                        Button("Refresh") {
                            viewModel.loadItems()
                        }
                        .buttonStyle(.bordered)
                    }
                } else {
                    List(filteredItems) { item in
                        NavigationLink(
                            destination: FoodshareItemView(
                                item: item,
                                onDelete: {
                                    viewModel.deleteItem(item)
                                }
                            )
                        ) {
                            FoodshareRow(item: item)
                        }
                    }
                    .refreshable {
                        viewModel.loadItems()
                    }
                }
            }
            .navigationTitle("Foodshare")
            .onAppear {
                viewModel.loadItems()
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Menu {
                        Button("All Restrictions") { activeFilter = nil }
                        Divider()
                        ForEach(DietaryRestriction.allCases) { restriction in
                            Button(restriction.rawValue) {
                                activeFilter = restriction
                            }
                        }
                    } label: {
                        Label(
                            "Filter",
                            systemImage: activeFilter == nil ? "line.3.horizontal.decrease.circle" : "line.3.horizontal.decrease.circle.fill")
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingCreate = true }) {
                        Image(systemName: "plus")
                            .font(.title2)
                    }
                }
                
                ToolbarItem(placement: .bottomBar) {
                    Button("Logout") {
                        session.logout()
                    }
                    .foregroundColor(.red)
                }
            }
            .sheet(isPresented: $showingCreate) {
                FoodshareFormView(onComplete: {
                    viewModel.loadItems()
                })
            }
        }
    }
}

#Preview {
    FoodshareListView()
        .environmentObject(SessionManager.shared)
}
