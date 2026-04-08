//
//  CameraPicker.swift
//  BlackBearFoodShare
//

import SwiftUI
import UIKit

struct CameraPicker: UIViewControllerRepresentable {
    @Binding var imageData: Data?
    @Environment(\.dismiss) var dismiss

    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        let parent: CameraPicker

        init(_ parent: CameraPicker) {
            self.parent = parent
        }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            // Prefer edited image for the box crop
            if let uiImage = info[.editedImage] as? UIImage ?? info[.originalImage] as? UIImage {
                // Convert to data (JPEG with 0.8 compression)
                parent.imageData = uiImage.jpegData(compressionQuality: 0.8)
            }
            parent.dismiss()
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .camera
        picker.allowsEditing = true // This provides the square cropping UI
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
}
