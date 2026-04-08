//
//  SurveyView.swift
//  BlackBearFoodShare
//

import SwiftUI

struct SurveyView: View {
    let foodshareID: Int
    let onComplete: () -> Void
    let onCancel: () -> Void
    
    @Environment(\.dismiss) var dismiss
    @State private var numParticipants: Int = 1
    @State private var experience: Int = 5
    @State private var otherThoughts: String = ""
    @State private var isSubmitting: Bool = false
    @State private var errorMessage: String?
    
    private let service: FoodshareServiceProtocol
    
    init(foodshareID: Int, 
         service: FoodshareServiceProtocol? = nil,
         onComplete: @escaping () -> Void,
         onCancel: @escaping () -> Void) {
        self.foodshareID = foodshareID
        self.onComplete = onComplete
        self.onCancel = onCancel
        
        if let providedService = service {
            self.service = providedService
        } else {
            self.service = ProcessInfo.processInfo.arguments.contains("-UITest") ? MockFoodshareService() : FoodshareService()
        }
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Feedback")) {
                    Stepper("Participants: \(numParticipants)", value: $numParticipants, in: 0...100)
                    
                    VStack(alignment: .leading) {
                        Text("Experience")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        HStack {
                            ForEach(1...5, id: \.self) { star in
                                Image(systemName: star <= experience ? "star.fill" : "star")
                                    .foregroundColor(star <= experience ? .yellow : .gray)
                                    .onTapGesture {
                                        experience = star
                                    }
                                    .font(.title2)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Other Thoughts")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        TextEditor(text: $otherThoughts)
                            .frame(minHeight: 100)
                    }
                }
                
                if let error = errorMessage {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }
                
                Section {
                    Button(action: submitAndClose) {
                        if isSubmitting {
                            ProgressView()
                                .frame(maxWidth: .infinity)
                        } else {
                            Text("Submit & Close")
                                .bold()
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .disabled(isSubmitting)
                    .listRowBackground(Color.blue)
                    .foregroundColor(.white)
                    
                    Button(action: skipAndClose) {
                        Text("Skip & Close")
                            .frame(maxWidth: .infinity)
                    }
                    .disabled(isSubmitting)
                    .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Closing Foodshare")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        onCancel()
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func submitAndClose() {
        isSubmitting = true
        errorMessage = nil
        
        let survey = Survey(
            num_participants: numParticipants,
            experience: experience,
            other_thoughts: otherThoughts,
            foodshare_fk_id: foodshareID
        )
        
        Task {
            do {
                // 1. Submit Survey
                try await service.submitSurvey(survey)
                
                // 2. Close Foodshare
                try await service.closeFoodshare(id: foodshareID)
                
                // 3. Callback
                onComplete()
                dismiss()
            } catch {
                errorMessage = "Submission failed: \(error.localizedDescription)"
                isSubmitting = false
            }
        }
    }
    
    private func skipAndClose() {
        isSubmitting = true
        errorMessage = nil
        
        Task {
            do {
                try await service.closeFoodshare(id: foodshareID)
                onComplete()
                dismiss()
            } catch {
                errorMessage = "Failed to close: \(error.localizedDescription)"
                isSubmitting = false
            }
        }
    }
}

#Preview {
    SurveyView(foodshareID: 1, 
               service: MockFoodshareService(),
               onComplete: {}, 
               onCancel: {})
}
