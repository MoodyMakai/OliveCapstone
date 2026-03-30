//
//  FoodshareItemView.swift
//  BlackBearFoodShare
//

import SwiftUI

struct FoodshareItemView: View {
    let item: FoodshareItem
    var onDelete: (() -> Void)?
    
    @Environment(\.dismiss) var dismiss
    @Environment(\.openURL) var openURL
    @EnvironmentObject var session: SessionManager
    
    @State private var showDeleteConfirmation = false
    
    // Check if the current user is the creator of this foodshare
    private var isOwner: Bool {
        return session.currentUser?.id == item.creator?.id
    }
    
    private let dateFormatter: DateFormatter = {
        let df = DateFormatter()
        df.dateStyle = .none
        df.timeStyle = .short
        return df
    }()
    
    private var imageURL: URL? {
        guard let path = item.picture?.filepath else { return nil }
        if path.hasPrefix("http") {
            return URL(string: path)
        }
        return URL(string: "http://localhost:5000" + path)
    }
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                
                // IMAGE HANDLING
                AsyncImage(url: imageURL) { phase in
                    switch phase {
                    case .empty:
                        ZStack {
                            Color.gray.opacity(0.1)
                            ProgressView()
                        }
                        .frame(maxWidth: .infinity, minHeight: 300)
                        
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                            .frame(maxWidth: .infinity, minHeight: 300)
                            .clipped()
                        
                    case .failure:
                        ZStack {
                            Color.gray.opacity(0.3)
                            Image(systemName: "photo")
                                .font(.largeTitle)
                                .foregroundColor(.gray)
                        }
                        .frame(maxWidth: .infinity, minHeight: 300)
                        
                    @unknown default:
                        EmptyView()
                    }
                }

                // TEXT CONTENT
                VStack(alignment: .leading, spacing: 12) {
                    
                    Text(item.name)
                        .font(.largeTitle)
                        .bold()
                    
                    Text("Shared by \(item.creator?.email ?? "Unknown")")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    Divider()

                    // Restrictions
                    if !item.restrictions.isEmpty {
                        Text("Dietary Notes:")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)
                        
                        TagView(tags: item.restrictions)
                            .frame(maxWidth: .infinity, minHeight: 40)
                    }
                    
                    Divider()

                    // Location and Time Info
                    VStack(alignment: .leading, spacing: 10) {
                        
                        HStack {
                            Image(systemName: "clock")
                                .frame(width: 24)
                            Text("Ends at \(dateFormatter.string(from: item.endTime))")
                        }
                        .foregroundColor(.secondary)
                        
                        HStack {
                            Image(systemName: "building.2")
                                .frame(width: 24)
                                .foregroundColor(.secondary)
                            
                            Text(item.location)
                                .foregroundColor(.secondary)
                            
                            Spacer()
                            
                            Button {
                                let building = item.location.components(separatedBy: ",").first ?? item.location
                                if let url = BuildingLocator.shared.mapsURL(for: building) {
                                    openURL(url)
                                }
                            } label: {
                                HStack {
                                    Text("Maps")
                                        .fontWeight(.semibold)
                                    Image(systemName: "location.fill")
                                }
                                .padding(.vertical, 8)
                                .padding(.horizontal, 12)
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(20)
                            }
                        }
                    }
                    .font(.headline)
                }
                .padding(.horizontal)
                
                if isOwner {
                    Divider()
                        .padding(.horizontal)
                    Button(role: .destructive) {
                        showDeleteConfirmation = true
                    } label: {
                        HStack {
                            Spacer()
                            Label("Close Foodshare", systemImage: "xmark.circle")
                                .font(.headline)
                            Spacer()
                        }
                        .padding()
                        .background(Color.red)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                        .padding(.horizontal)
                    }
                    .alert("Close this foodshare?", isPresented: $showDeleteConfirmation) {
                        Button("Close", role: .destructive) {
                            onDelete?()
                            dismiss()
                        }
                        Button("Cancel", role: .cancel) { }
                    } message: {
                        Text("This will remove the listing from the app for everyone.")
                    }
                }
                
                Spacer()
            }
        }
        .ignoresSafeArea(edges: .top)
    }
}

#Preview {
    FoodshareItemView(item: sampleFoodshareItems[0])
        .environmentObject(SessionManager.preview)
}
