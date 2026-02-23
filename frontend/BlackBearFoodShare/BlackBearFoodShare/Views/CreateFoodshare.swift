//
//  CreateFoodshare.swift
//  BlackBearFoodShare
//
//  Created by Wesley Dumas on 12/7/25.
//

import SwiftUI

struct CreateFoodshare: View {
    @EnvironmentObject var store: FoodshareStore // Using EnvironmentObject for consistency
    @Environment(\.dismiss) private var dismiss
    
    @State private var name: String = ""
    @State private var description: String = ""
    @State private var building: String = ""
    @State private var classRoomNumber: String = ""
    @State private var imageURL: String = ""
    @State private var endTime: Date = Date()
    
    // Tracks multiple selections
    @State private var selectedRestrictions: Set<DietaryRestriction> = []

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Details")) {
                    TextField("Title (e.g. Free Pizza)", text: $name)
                    TextField("Description", text: $description)
                    TextField("Image URL", text: $imageURL)
                        .keyboardType(.URL)
                        .autocapitalization(.none)
                }
                
                Section(header: Text("Location")) {
                    TextField("Building Name", text: $building)
                    TextField("Room Number", text: $classRoomNumber)
                }
                Section(header: Text("Dietary Restrictions")) {
                    ForEach(DietaryRestriction.allCases) { restriction in
                        Toggle(restriction.rawValue, isOn: Binding(
                            get: { selectedRestrictions.contains(restriction) },
                            set: { isSelected in
                                if isSelected {
                                    selectedRestrictions.insert(restriction)
                                } else {
                                    selectedRestrictions.remove(restriction)
                                }
                            }
                        ))
                    }
                }
                
                Section {
                    DatePicker("End Time", selection: $endTime, displayedComponents: [.hourAndMinute])
                }
                
                Button(action: createAndDismiss) {
                    Text("Submit")
                        .frame(maxWidth: .infinity, alignment: .center)
                        .bold()
                }
                .disabled(name.isEmpty || building.isEmpty)
            }
            .navigationTitle("New Foodshare")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
    
    func createAndDismiss() {
        let restrictionsArray = selectedRestrictions.map { $0.rawValue }

        let newFoodshare = FoodshareItem(
            name: name,
            endTime: endTime,
            description: description,
            foodRestrictions: restrictionsArray,
            imageURL: imageURL,
            building: building,
            classRoomNumber: classRoomNumber
        )
        
        store.items.append(newFoodshare)
        dismiss()
    }
}

#Preview {
    CreateFoodshare()
}
