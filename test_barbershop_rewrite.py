#!/usr/bin/env python3
"""
COMPREHENSIVE BARBERSHOP API TESTING SCRIPT
Tests the rewritten barbershop data fetching logic for both Super Admin and Regular Admin
"""
import requests
import json
import time
from typing import Dict, List, Any


BASE_URL = "http://127.0.0.1:8000/api"

class BarbershopAPIValidator:
    def __init__(self):
        self.super_admin_token = None
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
        print()
    
    def login_super_admin(self) -> bool:
        """Login as super admin"""
        print("🔐 PHASE 1: Super Admin Authentication")
        
        credentials = [
            {"email": "19bmiit087@gmail.com", "password": "Super@123"},
            {"email": "admin@test.com", "password": "admin123"}
        ]
        
        for creds in credentials:
            try:
                response = requests.post(f"{BASE_URL}/auth/login/", json=creds)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and 'data' in data and 'access' in data['data']:
                        self.super_admin_token = data['data']['access']
                        self.log_test(
                            f"Super Admin Login ({creds['email']})",
                            "PASS",
                            {"email": creds['email'], "token_length": len(self.super_admin_token)}
                        )
                        return True
                    
            except Exception as e:
                self.log_test(
                    f"Super Admin Login ({creds['email']})",
                    "FAIL",
                    {"error": str(e)}
                )
        
        return False
    
    def login_admin(self) -> bool:
        """Login as regular admin"""
        print("🔐 PHASE 2: Regular Admin Authentication")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login/", json={
                "email": "taha.sadikot.m@gmail.com",
                "password": "Admin@123"
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data and 'access' in data['data']:
                    self.admin_token = data['data']['access']
                    self.log_test(
                        "Regular Admin Login",
                        "PASS",
                        {"email": "taha.sadikot.m@gmail.com", "token_length": len(self.admin_token)}
                    )
                    return True
                    
        except Exception as e:
            self.log_test(
                "Regular Admin Login",
                "FAIL",
                {"error": str(e)}
            )
        
        return False
    
    def test_super_admin_api(self) -> Dict[str, Any]:
        """Test Super Admin barbershop API"""
        print("🚀 PHASE 3: Super Admin API Testing")
        
        if not self.super_admin_token:
            self.log_test("Super Admin API", "SKIP", {"reason": "No token available"})
            return {}
            
        try:
            headers = {"Authorization": f"Bearer {self.super_admin_token}"}
            url = f"{BASE_URL}/super-admin/barbershops/"
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=30)
            request_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if data.get('success') == True and 'data' in data:
                    barbershops = data['data']
                    count = data.get('count', 0)
                    
                    self.log_test(
                        "Super Admin API Response",
                        "PASS",
                        {
                            "status_code": response.status_code,
                            "response_time_ms": f"{request_time:.0f}",
                            "barbershops_count": len(barbershops),
                            "reported_count": count,
                            "has_metadata": "metadata" in data,
                            "endpoint": data.get("metadata", {}).get("endpoint", "unknown")
                        }
                    )
                    
                    # Validate barbershop data structure
                    if barbershops and len(barbershops) > 0:
                        sample_shop = barbershops[0]
                        required_fields = ['id', 'email', 'shop_name', 'is_active']
                        missing_fields = [field for field in required_fields if field not in sample_shop]
                        
                        self.log_test(
                            "Super Admin Data Structure",
                            "PASS" if not missing_fields else "FAIL",
                            {
                                "sample_shop_id": sample_shop.get('id'),
                                "sample_shop_name": sample_shop.get('shop_name'),
                                "missing_fields": missing_fields or "None"
                            }
                        )
                    
                    return {
                        "success": True,
                        "barbershops": barbershops,
                        "count": count,
                        "response_data": data
                    }
                else:
                    self.log_test(
                        "Super Admin API Response",
                        "FAIL",
                        {"reason": "Invalid response structure", "response": data}
                    )
            else:
                self.log_test(
                    "Super Admin API Response",
                    "FAIL",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_test(
                "Super Admin API",
                "FAIL",
                {"error": str(e)}
            )
        
        return {"success": False}
    
    def test_admin_api(self) -> Dict[str, Any]:
        """Test Regular Admin barbershop API"""
        print("🚀 PHASE 4: Regular Admin API Testing")
        
        if not self.admin_token:
            self.log_test("Regular Admin API", "SKIP", {"reason": "No token available"})
            return {}
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            url = f"{BASE_URL}/admin/barbershops/"
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=30)
            request_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if data.get('success') == True and 'data' in data:
                    barbershops = data['data']
                    count = data.get('count', 0)
                    
                    self.log_test(
                        "Regular Admin API Response",
                        "PASS",
                        {
                            "status_code": response.status_code,
                            "response_time_ms": f"{request_time:.0f}",
                            "barbershops_count": len(barbershops),
                            "reported_count": count,
                            "has_metadata": "metadata" in data,
                            "endpoint": data.get("metadata", {}).get("endpoint", "unknown")
                        }
                    )
                    
                    # Validate barbershop data structure
                    if barbershops and len(barbershops) > 0:
                        sample_shop = barbershops[0]
                        required_fields = ['id', 'email', 'shop_name', 'is_active']
                        missing_fields = [field for field in required_fields if field not in sample_shop]
                        
                        self.log_test(
                            "Regular Admin Data Structure",
                            "PASS" if not missing_fields else "FAIL",
                            {
                                "sample_shop_id": sample_shop.get('id'),
                                "sample_shop_name": sample_shop.get('shop_name'),
                                "missing_fields": missing_fields or "None"
                            }
                        )
                    
                    return {
                        "success": True,
                        "barbershops": barbershops,
                        "count": count,
                        "response_data": data
                    }
                else:
                    self.log_test(
                        "Regular Admin API Response",
                        "FAIL",
                        {"reason": "Invalid response structure", "response": data}
                    )
            else:
                self.log_test(
                    "Regular Admin API Response",
                    "FAIL",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_test(
                "Regular Admin API",
                "FAIL",
                {"error": str(e)}
            )
        
        return {"success": False}
    
    def validate_role_based_filtering(self, super_admin_result: Dict, admin_result: Dict):
        """Validate that role-based filtering works correctly"""
        print("🚀 PHASE 5: Role-based Filtering Validation")
        
        if not super_admin_result.get("success") or not admin_result.get("success"):
            self.log_test(
                "Role-based Filtering",
                "SKIP",
                {"reason": "One or both APIs failed"}
            )
            return
        
        super_admin_count = super_admin_result.get("count", 0)
        admin_count = admin_result.get("count", 0)
        
        # Super admin should see equal or more barbershops than regular admin
        if super_admin_count >= admin_count:
            self.log_test(
                "Role-based Filtering Logic",
                "PASS",
                {
                    "super_admin_count": super_admin_count,
                    "admin_count": admin_count,
                    "difference": super_admin_count - admin_count
                }
            )
        else:
            self.log_test(
                "Role-based Filtering Logic",
                "FAIL",
                {
                    "super_admin_count": super_admin_count,
                    "admin_count": admin_count,
                    "issue": "Admin sees more barbershops than Super Admin"
                }
            )
        
        # Check if admin barbershops are subset of super admin barbershops
        admin_barbershops = admin_result.get("barbershops", [])
        super_admin_barbershops = super_admin_result.get("barbershops", [])
        
        admin_ids = {shop.get('id') for shop in admin_barbershops}
        super_admin_ids = {shop.get('id') for shop in super_admin_barbershops}
        
        if admin_ids.issubset(super_admin_ids):
            self.log_test(
                "Data Consistency Check",
                "PASS",
                {"admin_barbershops_in_super_admin": "All admin barbershops found in super admin results"}
            )
        else:
            missing_ids = admin_ids - super_admin_ids
            self.log_test(
                "Data Consistency Check",
                "FAIL",
                {"missing_barbershop_ids": list(missing_ids)}
            )
    
    def generate_report(self):
        """Generate final test report"""
        print("📊 FINAL REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  ❌ {result['test_name']}: {result['details']}")
            print()
        
        if passed_tests == total_tests - skipped_tests:
            print("🎉 ALL TESTS PASSED! Barbershop data fetching is working correctly.")
        elif failed_tests == 0:
            print("✅ No failures, but some tests were skipped.")
        else:
            print("⚠️ Some tests failed. Please review the issues above.")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 STARTING COMPREHENSIVE BARBERSHOP API VALIDATION")
        print("=" * 60)
        
        # Phase 1: Authentication
        super_admin_auth = self.login_super_admin()
        admin_auth = self.login_admin()
        
        if not super_admin_auth and not admin_auth:
            print("❌ CRITICAL: No authentication successful. Cannot proceed.")
            return
        
        # Phase 2: API Testing
        super_admin_result = self.test_super_admin_api()
        admin_result = self.test_admin_api()
        
        # Phase 3: Validation
        self.validate_role_based_filtering(super_admin_result, admin_result)
        
        # Phase 4: Report
        self.generate_report()


if __name__ == "__main__":
    validator = BarbershopAPIValidator()
    validator.run_comprehensive_test()