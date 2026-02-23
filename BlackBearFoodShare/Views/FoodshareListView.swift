//
//  FoodshareListView.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 12/1/25.
//

import SwiftUI

struct FoodshareListView: View {
    @EnvironmentObject var store: FoodshareStore
    @State private var showingCreate = false
    @State private var activeFilter: DietaryRestriction? = nil

    // Computed property to filter the list dynamically
    var filteredItems: [FoodshareItem] {
        if let filter = activeFilter {
            return store.items.filter { $0.foodRestrictions.contains(filter.rawValue) }
        }
        return store.items
    }

    var body: some View {
        NavigationView {
            List(filteredItems) { item in
                NavigationLink(destination: Text("Detail View for \(item.name)")) {
                    FoodshareRow(item: item)
                }
            }
            .navigationTitle("Foodshare")
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
                        Label("Filter", systemImage: activeFilter == nil ? "line.3.horizontal.decrease.circle" : "line.3.horizontal.decrease.circle.fill")
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingCreate = true }) {
                        Image(systemName: "plus")
                            .font(.title2)
                    }
                }
            }
            .sheet(isPresented: $showingCreate) {
                FoodShareCreationView()
            }
        }
    }
}

struct SDataWrapper {
    var store: FoodshareStore
    var foodshareItems: [FoodshareItem] {
        get { store.items }
        set { store.items = newValue }
    }
}


#Preview {
    FoodshareListView().environmentObject(FoodshareStore())
}
