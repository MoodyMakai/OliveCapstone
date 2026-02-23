//
//  FoodshareRow.swift
//  BlackBearFoodShare
//
//  Created by Corey Kaulenas on 12/1/25.
//


import SwiftUI

struct FoodshareRow: View {
    let item: FoodshareItem
    let formatter: DateFormatter = {
        let f = DateFormatter()
        f.timeStyle = .short
        return f
    }()
    
    var body: some View {
        VStack {
            AsyncImage(url: URL(string: item.imageURL)) { image in
                image.resizable().scaledToFill()
            } placeholder: {
                ProgressView()
            }
            .frame(width: 300, height: 300)
            .clipShape(RoundedRectangle(cornerRadius: 10))

            VStack(alignment: .leading) {
                Text(item.name).font(.largeTitle)
                Text("Ends at: \(formatter.string(from: item.endTime))")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
            Spacer()
        }
        .padding(.vertical, 6)
    }
}

#Preview {
    FoodshareRow(item: sampleFoodshareItems[0])
}
