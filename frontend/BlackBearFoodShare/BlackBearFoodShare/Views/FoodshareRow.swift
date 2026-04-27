//
//  FoodshareRow.swift
//  BlackBearFoodShare
//

import SwiftUI

struct FoodshareRow: View {
    let item: FoodshareItem
    let formatter: DateFormatter = {
        let f = DateFormatter()
        f.timeStyle = .short
        return f
    }()
    
    private var imageURL: URL? {
        guard let path = item.picture?.filepath else { return nil }
        if path.hasPrefix("http") {
            return URL(string: path)
        }
        // Load API base URL from Info.plist configuration
        guard let baseURL = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String else {
            return nil
        }
        let cleanBaseURL = baseURL.replacingOccurrences(of: "\\", with: "")
        return URL(string: cleanBaseURL + path)
    }
    
    var body: some View {
        VStack {
            AsyncImage(url: imageURL) { image in
                image
                    .resizable()
                    .scaledToFill()
                    .frame(width: 300, height: 300)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
            } placeholder: {
                ProgressView()
                    .frame(width: 300, height: 300)
            }

            VStack(alignment: .leading) {
                Text(item.name)
                    .font(.headline)
                Text("Ends at: \(formatter.string(from: item.endTime))")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
            .frame(maxWidth: 300, alignment: .leading)
            
            Spacer()
        }
        .padding(.vertical, 6)
    }
}

#Preview {
    FoodshareRow(item: sampleFoodshareItems[0])
}
