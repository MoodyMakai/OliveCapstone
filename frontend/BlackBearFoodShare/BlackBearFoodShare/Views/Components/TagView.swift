//
//  TagView.swift
//  BlackBearFoodShare
//

import SwiftUI

/// A view that displays a collection of tags in a flowing layout.
struct TagView: View {
    let tags: [String]
    
    var body: some View {
        // Using a simple wrapping algorithm for iOS 16+ Flow Layout
        // If we wanted to be very precise we'd use the Layout protocol,
        // but for an audit/refactor, a clean HStack/VStack combo or a third-party style approach works.
        // Here we use a standard HStack with wrapping simulation if possible, 
        // or just a clean horizontal scroll if preferred.
        // For "Flow", we'll implement a basic geometry-based wrap.
        
        GeometryReader { geometry in
            self.generateContent(in: geometry)
        }
        .frame(minHeight: 40) // Adjust as needed
    }

    private func generateContent(in g: GeometryProxy) -> some View {
        var width = CGFloat.zero
        var height = CGFloat.zero

        return ZStack(alignment: .topLeading) {
            ForEach(self.tags, id: \.self) { tag in
                self.item(for: tag)
                    .padding([.horizontal, .vertical], 4)
                    .alignmentGuide(.leading, computeValue: { d in
                        if (abs(width - d.width) > g.size.width) {
                            width = 0
                            height -= d.height
                        }
                        let result = width
                        if tag == self.tags.last! {
                            width = 0 // last item
                        } else {
                            width -= d.width
                        }
                        return result
                    })
                    .alignmentGuide(.top, computeValue: { d in
                        let result = height
                        if tag == self.tags.last! {
                            height = 0 // last item
                        }
                        return result
                    })
            }
        }
    }

    private func item(for text: String) -> some View {
        HStack(spacing: 4) {
            Image(systemName: "checkmark.circle.fill")
            Text(text)
        }
        .padding(.vertical, 4)
        .padding(.horizontal, 8)
        .background(Color.green.opacity(0.1))
        .foregroundColor(.green)
        .font(.caption)
        .cornerRadius(8)
    }
}
