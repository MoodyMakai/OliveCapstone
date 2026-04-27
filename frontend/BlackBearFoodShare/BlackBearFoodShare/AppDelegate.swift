//
//  AppDelegate.swift
//  

import UIKit
import UserNotifications

final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {

        UNUserNotificationCenter.current().delegate = self

        // TODO: Re-enable push notifications when deploying to production
        // Push notifications require proper provisioning profiles and aps-environment entitlement
        // Task {
        //     let center = UNUserNotificationCenter.current()
        //     do {
        //         let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge, .provisional])
        //         print("Notifications Allowed: \(granted)")
        //
        //         await MainActor.run {
        //             UIApplication.shared.registerForRemoteNotifications()
        //         }
        //     } catch {
        //         print("error: \(error)")
        //     }
        // }

        return true
    }

    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        print("device token: \(deviceToken)")
        //send tokenString to server
    }

    func application(_ application: UIApplication,
                     didFailToRegisterForRemoteNotificationsWithError error: Error) {
        print("Failed to register for remote notifications: \(error)")
    }
}

