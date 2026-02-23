//
//  FoodShareCreationView.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 12/7/25.
//
import SwiftUI

struct FoodShareCreationView: View {
    @EnvironmentObject var store: FoodshareStore
    @Environment(\.dismiss) var dismiss
    
    @State private var foodshareName: String = ""
    @State private var selectedBuilding: String = ""
    @State private var classroomNumber: String = ""
    @State private var descriptionText: String = ""
    @State private var imageURL: String = ""
    @State private var endTime: Date = Date()
    
    // Updated to use the Set of our Enum for type-safety
    @State private var selectedRestrictions: Set<DietaryRestriction> = []

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Basic Info")) {
                    TextField("Foodshare Name", text: $foodshareName)
                    TextField("Image URL", text: $imageURL)
                        .keyboardType(.URL)
                        .autocapitalization(.none)

                    DatePicker("Ends At", selection: $endTime)
                }

                Section(header: Text("Location")) {
                    Picker("Building", selection: $selectedBuilding) {
                        Text("Select a building").tag("") // Placeholder
                        ForEach(BuildingLocator.shared.allAliases(), id: \.self) { building in
                            Text(building).tag(building)
                        }
                    }

                    TextField("Classroom Number", text: $classroomNumber)
                        .keyboardType(.numbersAndPunctuation)
                }

                Section(header: Text("Description")) {
                    TextEditor(text: $descriptionText)
                        .frame(minHeight: 100)
                }

                // New logic: Pre-defined toggle list to prevent typos
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
                    Button(action: saveFoodshare) {
                        HStack {
                            Spacer()
                            Text("Save Foodshare")
                                .bold()
                            Spacer()
                        }
                    }
                    .disabled(foodshareName.isEmpty || selectedBuilding.isEmpty)
                }
            }
            .navigationTitle("New Foodshare")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }

    private func saveFoodshare() {
        let restrictionsArray = selectedRestrictions.map { $0.rawValue }

        let item = FoodshareItem(
            name: foodshareName,
            endTime: endTime,
            description: descriptionText,
            foodRestrictions: restrictionsArray,
            imageURL: imageURL,
            building: selectedBuilding,
            classRoomNumber: classroomNumber
        )

        store.add(item)
        dismiss()
    }
}

#Preview {
    FoodShareCreationView()
}
