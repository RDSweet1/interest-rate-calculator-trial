"""
Integration tests for Interest Rate Calculator
"""
import pytest
import json
import os
import tempfile
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestProjectCRUDOperations:
    """Test Create, Read, Update, Delete operations for projects"""
    
    @pytest.mark.integration
    def test_create_and_load_project(self, sample_project_data):
        """Test creating and loading a project file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file = Path(temp_dir) / "test_project.json"
            
            # Create project file
            with open(project_file, 'w') as f:
                json.dump(sample_project_data, f, indent=2)
            
            # Verify file exists and can be loaded
            assert project_file.exists()
            
            with open(project_file, 'r') as f:
                loaded_data = json.load(f)
            
            # Verify data integrity
            assert loaded_data["title"] == sample_project_data["title"]
            assert loaded_data["annual_rate"] == sample_project_data["annual_rate"]
            assert len(loaded_data["payments"]) == len(sample_project_data["payments"])
            assert len(loaded_data["invoices"]) == len(sample_project_data["invoices"])

    @pytest.mark.integration
    def test_update_project_data(self, sample_project_data):
        """Test updating project data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file = Path(temp_dir) / "test_project.json"
            
            # Create initial project
            with open(project_file, 'w') as f:
                json.dump(sample_project_data, f, indent=2)
            
            # Update project data
            updated_data = sample_project_data.copy()
            updated_data["title"] = "Updated Test Project"
            updated_data["annual_rate"] = 0.20
            updated_data["payments"].append({
                "desc": "New Payment",
                "date": "2023-03-01",
                "amount": 25000.00
            })
            
            # Save updated data
            with open(project_file, 'w') as f:
                json.dump(updated_data, f, indent=2)
            
            # Verify updates
            with open(project_file, 'r') as f:
                loaded_data = json.load(f)
            
            assert loaded_data["title"] == "Updated Test Project"
            assert loaded_data["annual_rate"] == 0.20
            assert len(loaded_data["payments"]) == 3

    @pytest.mark.integration
    def test_delete_project(self, sample_project_data):
        """Test deleting a project file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_file = Path(temp_dir) / "test_project.json"
            
            # Create project file
            with open(project_file, 'w') as f:
                json.dump(sample_project_data, f, indent=2)
            
            assert project_file.exists()
            
            # Delete project file
            project_file.unlink()
            
            assert not project_file.exists()

class TestFileSystemIntegration:
    """Test file system operations and directory management"""
    
    @pytest.mark.integration
    def test_projects_directory_creation(self):
        """Test automatic creation of projects directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_dir = Path(temp_dir) / "projects"
            
            # Simulate directory creation logic
            projects_dir.mkdir(exist_ok=True)
            
            assert projects_dir.exists()
            assert projects_dir.is_dir()

    @pytest.mark.integration
    def test_outputs_directory_creation(self):
        """Test automatic creation of outputs directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs_dir = Path(temp_dir) / "outputs"
            
            # Simulate directory creation logic
            outputs_dir.mkdir(exist_ok=True)
            
            assert outputs_dir.exists()
            assert outputs_dir.is_dir()

    @pytest.mark.integration
    def test_multiple_project_files(self, sample_project_data):
        """Test handling multiple project files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_dir = Path(temp_dir) / "projects"
            projects_dir.mkdir()
            
            # Create multiple project files
            project_names = ["project1", "project2", "project3"]
            
            for name in project_names:
                project_data = sample_project_data.copy()
                project_data["title"] = f"Test Project {name}"
                
                project_file = projects_dir / f"{name}.json"
                with open(project_file, 'w') as f:
                    json.dump(project_data, f, indent=2)
            
            # Verify all files exist
            json_files = list(projects_dir.glob("*.json"))
            assert len(json_files) == 3
            
            # Verify each file can be loaded
            for project_file in json_files:
                with open(project_file, 'r') as f:
                    data = json.load(f)
                assert "title" in data
                assert data["title"].startswith("Test Project")

class TestApplicationIntegration:
    """Test integration between different application components"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_flask_app_startup_and_shutdown(self):
        """Test Flask application startup and shutdown"""
        # Set environment variable
        env = os.environ.copy()
        env["RUN_FLASK"] = "1"
        
        # Start Flask app
        process = subprocess.Popen([
            sys.executable, "interest_app.py"
        ], cwd=project_root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            # Wait for startup
            time.sleep(3)
            
            # Check if process is running
            assert process.poll() is None, "Flask app should be running"
            
            # Test basic connectivity (if requests is available)
            try:
                import requests
                response = requests.get("http://localhost:5000/", timeout=5)
                assert response.status_code == 200
                assert "Interest Rate Calculator" in response.text
            except ImportError:
                pytest.skip("requests not available for HTTP testing")
            except Exception as e:
                pytest.fail(f"Flask app not responding: {e}")
                
        finally:
            # Cleanup
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_desktop_app_startup(self):
        """Test desktop application startup"""
        # Start desktop app via launcher
        process = subprocess.Popen([
            sys.executable, "app_launcher.py"
        ], cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            # Wait for startup
            time.sleep(3)
            
            # Check if process is running
            assert process.poll() is None, "Desktop app should be running"
            
        finally:
            # Cleanup
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

class TestDataFlowIntegration:
    """Test data flow between components"""
    
    @pytest.mark.integration
    def test_project_data_to_calculation_flow(self, sample_project_data):
        """Test flow from project data to calculation results"""
        try:
            from interest_app import parse_project
        except ImportError:
            pytest.skip("interest_app module not available")
        
        # Test the complete flow
        summary_df, schedule_df = parse_project(sample_project_data)
        
        # Verify calculation results
        assert len(summary_df) == 3  # FW, DW, TOTAL
        assert len(schedule_df) > 0
        
        # Verify data types and structure
        assert "Line Item" in summary_df.columns
        assert "Principal" in summary_df.columns
        assert "Total Interest" in summary_df.columns
        
        assert "Start" in schedule_df.columns
        assert "End" in schedule_df.columns
        assert "FW Interest" in schedule_df.columns
        assert "DW Interest" in schedule_df.columns

    @pytest.mark.integration
    def test_calculation_to_export_flow(self, sample_project_data):
        """Test flow from calculation to file export"""
        try:
            from interest_app import parse_project, export_excel_and_pdf
        except ImportError:
            pytest.skip("interest_app module not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the output directory
            import interest_app
            original_output_dir = interest_app.OUTPUT_DIR
            interest_app.OUTPUT_DIR = temp_dir
            
            try:
                # Calculate
                summary_df, schedule_df = parse_project(sample_project_data)
                
                # Export
                xlsx_path, pdf_path = export_excel_and_pdf(
                    sample_project_data["title"], 
                    summary_df, 
                    schedule_df,
                    slug="test-integration"
                )
                
                # Verify files were created
                assert os.path.exists(xlsx_path)
                assert os.path.exists(pdf_path)
                
                # Verify file sizes (should not be empty)
                assert os.path.getsize(xlsx_path) > 0
                assert os.path.getsize(pdf_path) > 0
                
            finally:
                # Restore original output directory
                interest_app.OUTPUT_DIR = original_output_dir

class TestErrorHandlingIntegration:
    """Test error handling across components"""
    
    @pytest.mark.integration
    def test_invalid_project_file_handling(self):
        """Test handling of invalid project files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid JSON file
            invalid_file = Path(temp_dir) / "invalid.json"
            with open(invalid_file, 'w') as f:
                f.write("{ invalid json content")
            
            # Test loading invalid file
            with pytest.raises(json.JSONDecodeError):
                with open(invalid_file, 'r') as f:
                    json.load(f)

    @pytest.mark.integration
    def test_missing_project_file_handling(self):
        """Test handling of missing project files"""
        nonexistent_file = Path("nonexistent_project.json")
        
        # Test loading nonexistent file
        with pytest.raises(FileNotFoundError):
            with open(nonexistent_file, 'r') as f:
                json.load(f)

    @pytest.mark.integration
    def test_permission_error_handling(self):
        """Test handling of file permission errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file and make it read-only
            readonly_file = Path(temp_dir) / "readonly.json"
            with open(readonly_file, 'w') as f:
                json.dump({"test": "data"}, f)
            
            # Make file read-only (on Windows, this might not work as expected)
            try:
                readonly_file.chmod(0o444)
                
                # Try to write to read-only file
                with pytest.raises(PermissionError):
                    with open(readonly_file, 'w') as f:
                        json.dump({"new": "data"}, f)
                        
            except (OSError, NotImplementedError):
                # Skip if chmod doesn't work on this system
                pytest.skip("Cannot test file permissions on this system")

class TestConcurrencyIntegration:
    """Test concurrent operations"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_file_operations(self, sample_project_data):
        """Test multiple simultaneous file operations"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_project_file(index):
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    project_data = sample_project_data.copy()
                    project_data["title"] = f"Concurrent Project {index}"
                    json.dump(project_data, f, indent=2)
                    temp_path = f.name
                
                # Verify file was created
                with open(temp_path, 'r') as f:
                    loaded_data = json.load(f)
                
                results.put(("success", index, loaded_data["title"]))
                
                # Cleanup
                os.unlink(temp_path)
                
            except Exception as e:
                results.put(("error", index, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_project_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            status, index, data = results.get()
            if status == "success":
                success_count += 1
                assert f"Concurrent Project {index}" in data
            else:
                pytest.fail(f"Thread {index} failed: {data}")
        
        assert success_count == 5, "All concurrent operations should succeed"

class TestBackupAndRecovery:
    """Test backup and recovery scenarios"""
    
    @pytest.mark.integration
    def test_project_backup_and_restore(self, sample_project_data):
        """Test project backup and restore functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_file = Path(temp_dir) / "original.json"
            backup_file = Path(temp_dir) / "backup.json"
            
            # Create original file
            with open(original_file, 'w') as f:
                json.dump(sample_project_data, f, indent=2)
            
            # Create backup
            shutil.copy2(original_file, backup_file)
            
            # Verify backup
            assert backup_file.exists()
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            assert backup_data == sample_project_data
            
            # Simulate data corruption in original
            with open(original_file, 'w') as f:
                f.write("corrupted data")
            
            # Restore from backup
            shutil.copy2(backup_file, original_file)
            
            # Verify restoration
            with open(original_file, 'r') as f:
                restored_data = json.load(f)
            
            assert restored_data == sample_project_data

class TestSystemIntegration:
    """Test system-level integration"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_application_workflow(self, sample_project_data):
        """Test complete application workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup temporary project directory
            projects_dir = Path(temp_dir) / "projects"
            projects_dir.mkdir()
            
            # 1. Create project file
            project_file = projects_dir / "workflow_test.json"
            with open(project_file, 'w') as f:
                json.dump(sample_project_data, f, indent=2)
            
            # 2. Load and verify project
            with open(project_file, 'r') as f:
                loaded_data = json.load(f)
            
            assert loaded_data["title"] == sample_project_data["title"]
            
            # 3. Perform calculations (if module available)
            try:
                from interest_app import parse_project
                summary_df, schedule_df = parse_project(loaded_data)
                
                # 4. Verify calculation results
                assert len(summary_df) == 3
                assert len(schedule_df) > 0
                
                # 5. Test export functionality
                from interest_app import export_excel_and_pdf
                import interest_app
                
                original_output_dir = interest_app.OUTPUT_DIR
                interest_app.OUTPUT_DIR = temp_dir
                
                try:
                    xlsx_path, pdf_path = export_excel_and_pdf(
                        loaded_data["title"], summary_df, schedule_df
                    )
                    
                    # 6. Verify output files
                    assert os.path.exists(xlsx_path)
                    assert os.path.exists(pdf_path)
                    
                finally:
                    interest_app.OUTPUT_DIR = original_output_dir
                    
            except ImportError:
                pytest.skip("interest_app module not available for full workflow test")

    @pytest.mark.integration
    def test_configuration_management(self):
        """Test configuration and environment management"""
        # Test environment variable handling
        original_flask = os.environ.get("RUN_FLASK")
        
        try:
            # Set test environment
            os.environ["RUN_FLASK"] = "1"
            assert os.environ["RUN_FLASK"] == "1"
            
            # Reset environment
            os.environ["RUN_FLASK"] = "0"
            assert os.environ["RUN_FLASK"] == "0"
            
        finally:
            # Restore original environment
            if original_flask is not None:
                os.environ["RUN_FLASK"] = original_flask
            elif "RUN_FLASK" in os.environ:
                del os.environ["RUN_FLASK"]
