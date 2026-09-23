/* TK-101 risk-annotated SysML v2 model.
 * PUNDIT: 2020-1.2.3-EUREKA-2022-00021
 * Synthetic teaching/demonstration assumptions, not measured plant data.
 * Risk expressions are engineering annotations, not inferred from topology.
 */
package TK101Study {
    private import ScalarValues::*;
    attribute PROJECT_ID : String = "2020-1.2.3-EUREKA-2022-00021";
    attribute DATA_STATUS : String = "synthetic educational data";

    part def SafetyComponent {
        attribute componentType : String;
        attribute functionName : String;
        attribute failureId : String;
        attribute failureLabel : String;
        attribute failureMode : String;
        attribute probability : Real;
        attribute failed : Boolean;
    }
    part def RiskEvent {
        attribute label : String;
        attribute probability : Real;
        attribute occurs : Boolean;
    }

    part TK101 : SafetyComponent {
        attribute :>> componentType = "tank";
        attribute :>> functionName = "store_flammable_liquid";
        attribute :>> failureId = "TK101_LEAK";
        attribute :>> failureLabel = "Tank integrity failure";
        attribute :>> failureMode = "loss_of_integrity";
        attribute :>> probability = 0.0005;
    }
    part P101 : SafetyComponent {
        attribute :>> componentType = "pump";
        attribute :>> functionName = "feed_tank";
        attribute :>> failureId = "P101_EXCESS";
        attribute :>> failureLabel = "Excessive feed flow";
        attribute :>> failureMode = "excess_flow";
        attribute :>> probability = 0.03;
    }
    part LT101 : SafetyComponent {
        attribute :>> componentType = "level_transmitter";
        attribute :>> functionName = "measure_level";
        attribute :>> failureId = "LT101_LOW";
        attribute :>> failureLabel = "Level transmitter fouling or negative bias";
        attribute :>> failureMode = "failed_low";
        attribute :>> probability = 0.02;
    }
    part LSHH101 : SafetyComponent {
        attribute :>> componentType = "high_high_level_switch";
        attribute :>> functionName = "initiate_shutdown";
        attribute :>> failureId = "LSHH101_FOD";
        attribute :>> failureLabel = "High-high switch failure on demand";
        attribute :>> failureMode = "fail_on_demand";
        attribute :>> probability = 0.01;
    }
    part XV101 : SafetyComponent {
        attribute :>> componentType = "shutdown_valve";
        attribute :>> functionName = "stop_inflow";
        attribute :>> failureId = "XV101_FOD";
        attribute :>> failureLabel = "Shutdown valve fails to close on demand";
        attribute :>> failureMode = "fail_on_demand";
        attribute :>> probability = 0.005;
    }
    part HIGH_LEVEL_CHALLENGE : RiskEvent {
        attribute :>> label = "High-level process challenge";
        attribute :>> probability = 0.08;
    }
    part OPERATOR_MISS : RiskEvent {
        attribute :>> label = "No timely operator response";
        attribute :>> probability = 0.04;
    }
    part MAINT_OVERDUE : RiskEvent {
        attribute :>> label = "Maintenance overdue";
        attribute :>> probability = 0.12;
    }
    part IGNITION : RiskEvent {
        attribute :>> label = "Effective ignition source present";
        attribute :>> probability = 0.1;
    }
    part BUND_UNAVAILABLE : RiskEvent {
        attribute :>> label = "Liquid containment ineffective";
        attribute :>> probability = 0.02;
    }
    part FIRE_PROTECTION_FAIL : RiskEvent {
        attribute :>> label = "Fire protection ineffective";
        attribute :>> probability = 0.05;
    }
    attribute OVERFLOW : Boolean =
        HIGH_LEVEL_CHALLENGE.occurs
        and (LSHH101.failed or XV101.failed)
        and (LT101.failed or OPERATOR_MISS.occurs);
    attribute ESCALATED_FIRE : Boolean =
        OVERFLOW and IGNITION.occurs
        and (BUND_UNAVAILABLE.occurs or FIRE_PROTECTION_FAIL.occurs);
}
