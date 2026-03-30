//
//  FoodshareFormView.swift
//  BlackBearFoodShare
//

import SwiftUI
import PhotosUI

@MainActor
struct FoodshareFormView: View {
    @Environment(\.dismiss) var dismiss
    
    // Dependencies
    private let service: FoodshareServiceProtocol
    var onComplete: () -> Void
    
    init(service: FoodshareServiceProtocol, onComplete: @escaping () -> Void) {
        self.service = service
        self.onComplete = onComplete
    }
    
    init(onComplete: @escaping () -> Void) {
        self.init(service: FoodshareService(), onComplete: onComplete)
    }
    
    // State
    @State private var name: String = ""
    @State private var selectedBuilding: String = ""
    @State private var classroomNumber: String = ""
    @State private var endTime: Date = Date().addingTimeInterval(3600)
    @State private var selectedRestrictions: Set<DietaryRestriction> = []
    
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImageData: Data?
    
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            Form {
                Section("What's being shared?") {
                    TextField("Name (e.g. Free Pizza)", text: $name)
                    
                    PhotosPicker(selection: $selectedItem, matching: .images) {
                        if let data = selectedImageData, let uiImage = UIImage(data: data) {
                            Image(uiImage: uiImage)
                                .resizable()
                                .scaledToFit()
                                .frame(maxHeight: 200)
                        } else {
                            Label("Select a Photo", systemImage: "photo.on.rectangle")
                        }
                    }
                    .onChange(of: selectedItem) { newItem in
                        Task {
                            if let data = try? await newItem?.loadTransferable(type: Data.self) {
                                selectedImageData = data
                            }
                        }
                    }
                }
                
                Section("Where and when?") {
                    Picker("Building", selection: $selectedBuilding) {
                        Text("Select a building").tag("")
                        ForEach(BuildingLocator.shared.allAliases(), id: \.self) { building in
                            Text(building).tag(building)
                        }
                    }
                    
                    TextField("Room Number", text: $classroomNumber)
                    
                    DatePicker("Expires at", selection: $endTime, in: Date()..., displayedComponents: [.hourAndMinute, .date])
                }
                
                Section("Dietary Restrictions") {
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
                
                if let error = errorMessage {
                    Section {
                        Text(error).foregroundColor(.red)
                    }
                }
                
                Section {
                    Button(action: submit) {
                        if isLoading {
                            ProgressView().frame(maxWidth: .infinity)
                        } else {
                            Text("Create Foodshare")
                                .bold()
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .disabled(isLoading || name.isEmpty || selectedBuilding.isEmpty || selectedImageData == nil)
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
    
    private func submit() {
        guard let imageData = selectedImageData else { return }
        
        isLoading = true
        errorMessage = nil
        
        let fullLocation = "\(selectedBuilding), Room \(classroomNumber)"
        let restrictionsArray = selectedRestrictions.map { $0.rawValue }
        
        Task {
            do {
                _ = try await service.createFoodshare(
                    name: name,
                    location: fullLocation,
                    ends: endTime,
                    image: imageData,
                    restrictions: restrictionsArray
                )
                onComplete()
                dismiss()
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}

#Preview {
    FoodshareFormView(service: MockFoodshareService(), onComplete: {})
        .environmentObject(SessionManager.preview)
}
