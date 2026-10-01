rootProject.name = "screenshot-bench"

pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
        // viddik's wip snapshots (<version>.<run>), for runs against an unreleased fix. Filtered, so
        // nothing else is looked up there.
        maven("https://reposilite.kotlin.website/snapshots") {
            content { includeGroupAndSubgroups("io.github.youndie.viddik") }
        }
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        // viddik's wip snapshots (<version>.<run>), for runs against an unreleased fix. Filtered, so
        // nothing else is looked up there.
        maven("https://reposilite.kotlin.website/snapshots") {
            content { includeGroupAndSubgroups("io.github.youndie.viddik") }
        }
    }
}

// One set of composables, four harnesses. Every module compiles the same sources from `fixtures/`,
// so a difference in the numbers is a difference in the tool, not in what it renders.
include(":viddik")
include(":roborazzi-desktop")
include(":roborazzi-android")
include(":paparazzi")

// youndie/viddik#53: components in their own module, fixtures in a module with no main sources.
include(":components")
include(":viddik-split")
