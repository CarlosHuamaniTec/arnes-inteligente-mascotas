package com.vitalpaw.mainclient.repository;

import com.vitalpaw.mainclient.model.Pet;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PetRepository extends JpaRepository<Pet, Long> {
    Pet findByIdAndOwnerId(Long id, Long ownerId);
}